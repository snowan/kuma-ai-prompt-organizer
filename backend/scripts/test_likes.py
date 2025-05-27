#!/usr/bin/env python3
"""
Test script for the likes functionality.

This script demonstrates:
1. User registration
2. User login
3. Getting a list of prompts
4. Liking a prompt
5. Checking if a prompt is liked
6. Getting user's liked prompts
7. Unliking a prompt
"""
import asyncio
import httpx
import json
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:8000/api/v1"

class TestClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.headers: Dict[str, str] = {}
    
    async def register_user(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """Register a new user."""
        url = f"{self.base_url}/auth/register"
        data = {
            "username": username,
            "email": email,
            "password": password
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            return response.json()
    
    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login a user and store the access token."""
        url = f"{self.base_url}/auth/login"
        form_data = {
            "username": username,
            "password": password,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                data=form_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            data = response.json()
            if "access_token" in data:
                self.token = data["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
            return data
    
    async def get_prompts(self) -> Dict[str, Any]:
        """Get a list of prompts."""
        url = f"{self.base_url}/prompts"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            return response.json()
    
    async def like_prompt(self, prompt_id: int) -> Dict[str, Any]:
        """Like a prompt."""
        url = f"{self.base_url}/prompts/{prompt_id}/like"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers)
            return response.json()
    
    async def unlike_prompt(self, prompt_id: int) -> bool:
        """Unlike a prompt."""
        url = f"{self.base_url}/prompts/{prompt_id}/like"
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=self.headers)
            return response.status_code == 204
    
    async def check_liked(self, prompt_id: int) -> bool:
        """Check if the current user has liked a prompt."""
        url = f"{self.base_url}/prompts/{prompt_id}/liked"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            return response.json()
    
    async def get_my_likes(self) -> Dict[str, Any]:
        """Get the current user's liked prompts."""
        url = f"{self.base_url}/users/me/likes"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            return response.json()

async def main():
    print("=== Testing Likes Functionality ===\n")
    
    # Initialize test client
    client = TestClient()
    
    # Test user credentials
    test_user = {
        "username": "testuser_likes",
        "email": "test_likes@example.com",
        "password": "TestPass123!"
    }
    
    try:
        # 1. Register a new user
        print("1. Registering a new user...")
        register_result = await client.register_user(**test_user)
        print(f"   - Registration result: {json.dumps(register_result, indent=2)}\n")
        
        # 2. Login with the new user
        print("2. Logging in...")
        login_result = await client.login(test_user["username"], test_user["password"])
        print(f"   - Login result: {json.dumps(login_result, indent=2)}\n")
        
        # 3. Get list of prompts
        print("3. Getting list of prompts...")
        prompts = await client.get_prompts()
        print(f"   - Found {len(prompts.get('items', []))} prompts")
        
        if not prompts.get('items'):
            print("   - No prompts found. Please add some prompts first.")
            return
        
        # Get the first prompt
        prompt = prompts['items'][0]
        prompt_id = prompt['id']
        print(f"   - Selected prompt: {prompt['title']} (ID: {prompt_id})\n")
        
        # 4. Like the prompt
        print(f"4. Liking prompt {prompt_id}...")
        like_result = await client.like_prompt(prompt_id)
        print(f"   - Like result: {json.dumps(like_result, indent=2)}")
        
        # 5. Check if prompt is liked
        print(f"\n5. Checking if prompt {prompt_id} is liked...")
        is_liked = await client.check_liked(prompt_id)
        print(f"   - Is liked: {is_liked}")
        
        # 6. Get user's liked prompts
        print("\n6. Getting user's liked prompts...")
        my_likes = await client.get_my_likes()
        print(f"   - User has {len(my_likes)} liked prompts")
        if my_likes:
            print(f"   - First like: Prompt ID {my_likes[0]['prompt_id']} at {my_likes[0]['created_at']}")
        
        # 7. Unlike the prompt
        print(f"\n7. Unliking prompt {prompt_id}...")
        unlike_success = await client.unlike_prompt(prompt_id)
        print(f"   - Unlike successful: {unlike_success}")
        
        # 8. Verify unlike
        print(f"\n8. Verifying prompt {prompt_id} is unliked...")
        is_liked = await client.check_liked(prompt_id)
        print(f"   - Is liked: {is_liked}")
        
        print("\n=== Test completed successfully! ===")
        
    except Exception as e:
        print(f"\n=== Test failed: {str(e)} ===")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
