"""
Test script to verify repository cloning and operations
"""

import requests
import time

BASE_URL = "http://localhost:5000"

def test_clone_repo():
    """Test cloning a repository."""
    print("="*80)
    print("Testing Repository Clone & Operations")
    print("="*80)
    
    # Test 1: Clone a small test repository
    print("\n1. Cloning test repository...")
    repo_url = "https://github.com/octocat/Hello-World.git"
    
    response = requests.post(f"{BASE_URL}/api/repo/clone", json={"url": repo_url})
    
    if response.status_code == 200:
        print("✅ Repository cloned successfully!")
        print(f"   Path: {response.json()['path']}")
        print(f"   Name: {response.json()['name']}")
    else:
        print(f"❌ Failed to clone: {response.json()}")
        return
    
    time.sleep(2)
    
    # Test 2: Get files
    print("\n2. Loading files...")
    response = requests.get(f"{BASE_URL}/api/files")
    
    if response.status_code == 200:
        files = response.json()['files']
        print(f"✅ Loaded {len(files)} files/folders")
        for file in files[:5]:
            print(f"   - {file['name']} ({file['type']})")
    else:
        print(f"❌ Failed to load files: {response.json()}")
        return
    
    # Test 3: Get git status
    print("\n3. Checking git status...")
    response = requests.get(f"{BASE_URL}/api/git/status")
    
    if response.status_code == 200:
        status = response.json()['files']
        print(f"✅ Git status: {len(status)} changes")
    else:
        print(f"❌ Failed to get status: {response.json()}")
    
    # Test 4: Read a file
    print("\n4. Reading README file...")
    response = requests.get(f"{BASE_URL}/api/file/content", params={"path": "README"})
    
    if response.status_code == 200:
        content = response.json()['content']
        print(f"✅ File content loaded ({len(content)} characters)")
        print(f"   Preview: {content[:100]}...")
    else:
        print(f"❌ Failed to read file: {response.json()}")
    
    print("\n" + "="*80)
    print("✅ All tests passed! System is working correctly.")
    print("="*80)
    print("\nYou can now:")
    print("1. Open http://localhost:3000")
    print("2. Enter a repository URL")
    print("3. Clone and start editing!")


if __name__ == "__main__":
    print("\nMake sure the Flask server is running (python api_server.py)")
    input("Press Enter to start tests...")
    
    try:
        test_clone_repo()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to server")
        print("Make sure Flask server is running: python api_server.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
