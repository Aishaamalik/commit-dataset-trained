"""
Simple API wrapper for commit message generation
Can be used programmatically or as a module
"""

from commit_generator import CommitMessageGenerator
import sys


def generate_for_diff(diff_text, api_key=None):
    """Generate commit message for a given diff."""
    generator = CommitMessageGenerator(groq_api_key=api_key)
    return generator.generate_commit_message(diff_text=diff_text)


def generate_for_current_repo(api_key=None, custom_context=""):
    """Generate commit message for current repository's staged changes."""
    generator = CommitMessageGenerator(groq_api_key=api_key)
    return generator.generate_commit_message(custom_context=custom_context)


def interactive_mode():
    """Interactive mode with options."""
    print("="*80)
    print("AI Commit Message Generator - Interactive Mode")
    print("="*80)
    print("\nOptions:")
    print("1. Generate for staged changes")
    print("2. Generate for unstaged changes")
    print("3. Provide custom diff")
    print("4. Exit")
    
    try:
        generator = CommitMessageGenerator()
        
        while True:
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == '4':
                print("Goodbye!")
                break
            
            elif choice == '1':
                print("\nGenerating for staged changes...")
                result = generator.generate_commit_message()
                display_result(result)
            
            elif choice == '2':
                print("\nGenerating for unstaged changes...")
                diff = generator.get_git_diff(staged=False)
                result = generator.generate_commit_message(diff_text=diff)
                display_result(result)
            
            elif choice == '3':
                print("\nPaste your diff (press Ctrl+D or Ctrl+Z when done):")
                diff_lines = []
                try:
                    while True:
                        line = input()
                        diff_lines.append(line)
                except EOFError:
                    pass
                
                diff_text = '\n'.join(diff_lines)
                result = generator.generate_commit_message(diff_text=diff_text)
                display_result(result)
            
            else:
                print("Invalid option. Please select 1-4.")
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def display_result(result):
    """Display the generation result."""
    if "error" in result:
        print(f"\n❌ {result['error']}")
        return
    
    print("\n" + "="*80)
    print("GENERATED COMMIT MESSAGE:")
    print("="*80)
    print(result['commit_message'])
    
    print("\n" + "="*80)
    print("CHANGE SUMMARY:")
    print("="*80)
    print(f"Files: {len(result['analysis']['files_changed'])}")
    print(f"Added: +{result['analysis']['additions']} lines")
    print(f"Deleted: -{result['analysis']['deletions']} lines")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        # Default: generate for staged changes
        from commit_generator import main
        main()
