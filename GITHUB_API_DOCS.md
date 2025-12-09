# GitHub API Integration - Backend Documentation

## Overview
The backend now supports GitHub API integration for managing repositories, listing user repos, and uploading local projects to GitHub.

## Authentication
All GitHub API endpoints require a GitHub Personal Access Token (PAT) to be passed in the request headers:

```
X-GitHub-Token: your_github_token_here
```

### Getting a GitHub Token
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with these scopes:
   - `repo` (Full control of private repositories)
   - `delete_repo` (Delete repositories - optional)
   - `user` (Read user profile data)

## API Endpoints

### 1. Connect GitHub Account
**POST** `/api/github/connect`

Verify and store GitHub access token.

**Request Body:**
```json
{
  "token": "ghp_xxxxxxxxxxxx"
}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "login": "username",
    "id": 12345,
    "name": "User Name",
    "email": "user@example.com",
    "avatar_url": "https://...",
    "bio": "Developer"
  }
}
```

---

### 2. Get User Info
**GET** `/api/github/user`

Get authenticated GitHub user information.

**Headers:**
```
X-GitHub-Token: ghp_xxxxxxxxxxxx
```

**Response:**
```json
{
  "login": "username",
  "id": 12345,
  "name": "User Name",
  "email": "user@example.com",
  "avatar_url": "https://...",
  "public_repos": 25,
  "followers": 100,
  "following": 50
}
```

---

### 3. List Repositories
**GET** `/api/github/repos?page=1&per_page=30`

List user's GitHub repositories.

**Headers:**
```
X-GitHub-Token: ghp_xxxxxxxxxxxx
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Results per page (default: 30)

**Response:**
```json
{
  "repositories": [
    {
      "id": 123456,
      "name": "my-project",
      "full_name": "username/my-project",
      "description": "Project description",
      "private": false,
      "html_url": "https://github.com/username/my-project",
      "clone_url": "https://github.com/username/my-project.git",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T00:00:00Z",
      "language": "Python",
      "stargazers_count": 10,
      "forks_count": 2
    }
  ]
}
```

---

### 4. Create Repository
**POST** `/api/github/repos/create`

Create a new GitHub repository.

**Headers:**
```
X-GitHub-Token: ghp_xxxxxxxxxxxx
```

**Request Body:**
```json
{
  "name": "new-project",
  "description": "My new project",
  "private": false
}
```

**Response:**
```json
{
  "name": "new-project",
  "full_name": "username/new-project",
  "html_url": "https://github.com/username/new-project",
  "clone_url": "https://github.com/username/new-project.git",
  "ssh_url": "git@github.com:username/new-project.git"
}
```

---

### 5. Upload Local Project
**POST** `/api/github/upload`

Upload a local project to a new GitHub repository. This endpoint will:
1. Create a new repository on GitHub
2. Initialize git in the local directory (if needed)
3. Add all files
4. Commit changes
5. Push to GitHub

**Headers:**
```
X-GitHub-Token: ghp_xxxxxxxxxxxx
```

**Request Body:**
```json
{
  "local_path": "C:/Users/username/my-project",
  "repo_name": "my-project",
  "description": "My awesome project",
  "private": false,
  "commit_message": "Initial commit"
}
```

**Response:**
```json
{
  "message": "Project uploaded successfully",
  "repository": {
    "name": "my-project",
    "full_name": "username/my-project",
    "html_url": "https://github.com/username/my-project",
    "clone_url": "https://github.com/username/my-project.git",
    "ssh_url": "git@github.com:username/my-project.git"
  }
}
```

---

### 6. Delete Repository
**DELETE** `/api/github/repos/delete`

Delete a GitHub repository.

**Headers:**
```
X-GitHub-Token: ghp_xxxxxxxxxxxx
```

**Request Body:**
```json
{
  "owner": "username",
  "repo": "project-to-delete"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Repository deleted successfully"
}
```

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "error": "Error message description"
}
```

Common HTTP status codes:
- `400` - Bad Request (missing parameters, invalid data)
- `401` - Unauthorized (missing or invalid token)
- `404` - Not Found
- `500` - Internal Server Error

## Usage Example (JavaScript/Fetch)

```javascript
// Store token after GitHub OAuth
const token = 'ghp_xxxxxxxxxxxx';

// List repositories
const repos = await fetch('http://localhost:5000/api/github/repos', {
  headers: {
    'X-GitHub-Token': token
  }
});
const data = await repos.json();
console.log(data.repositories);

// Upload project
const upload = await fetch('http://localhost:5000/api/github/upload', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-GitHub-Token': token
  },
  body: JSON.stringify({
    local_path: 'C:/Users/me/my-project',
    repo_name: 'my-project',
    description: 'My awesome project',
    private: false
  })
});
const result = await upload.json();
console.log(result);
```

## Next Steps

The backend is ready. Now you need to:

1. **Frontend Integration**: Update React components to:
   - Store GitHub token from Firebase OAuth
   - Call these endpoints
   - Display repository list
   - Handle project upload with file picker

2. **Token Management**: Store the GitHub token securely (consider using Firebase to store it per user)

3. **UI Components**: Create screens for:
   - Repository listing
   - Project upload form
   - Success/error notifications
