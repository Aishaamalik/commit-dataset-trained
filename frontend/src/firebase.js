import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBP4kHfmsjmXTC5-CWDjx4lx5Fb8RYvZuc",
  authDomain: "autohub-ai-dfa5a.firebaseapp.com",
  projectId: "autohub-ai-dfa5a",
  storageBucket: "autohub-ai-dfa5a.firebasestorage.app",
  messagingSenderId: "680315548806",
  appId: "1:680315548806:web:753954883ae3717a680d07",
  measurementId: "G-QZXLXF1RFJ"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication and Firestore
export const auth = getAuth(app);
export const db = getFirestore(app);

/* 
FIRESTORE SECURITY RULES NEEDED:
To enable Firestore user data storage, add these rules in Firebase Console > Firestore Database > Rules:

rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow users to read/write their own user document
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}

After adding these rules, you can switch back from localStorage to Firestore in:
- userService.js
- Register.js  
- Login.js
*/

export default app;
