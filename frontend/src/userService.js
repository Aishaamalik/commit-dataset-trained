// Get user data from localStorage (temporary solution until Firestore rules are configured)
export const getUserData = async (userId) => {
  try {
    const username = localStorage.getItem(`user_${userId}_username`);
    if (username) {
      return {
        username: username,
        provider: 'local_storage' // temporary indicator
      };
    }
    return null;
  } catch (error) {
    console.error('Error getting user data:', error);
    throw error;
  }
};

// Create or update user data in localStorage (temporary solution)
export const saveUserData = async (userId, userData) => {
  try {
    if (userData.username) {
      localStorage.setItem(`user_${userId}_username`, userData.username);
    }
  } catch (error) {
    console.error('Error saving user data:', error);
    throw error;
  }
};

// Update specific user fields in localStorage (temporary solution)
export const updateUserData = async (userId, updates) => {
  try {
    if (updates.username) {
      localStorage.setItem(`user_${userId}_username`, updates.username);
    }
  } catch (error) {
    console.error('Error updating user data:', error);
    throw error;
  }
};