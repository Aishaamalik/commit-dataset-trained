import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

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

// Initialize Firebase Authentication
export const auth = getAuth(app);
export default app;
