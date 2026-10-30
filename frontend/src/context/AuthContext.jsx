
import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import {
  loginUser,
  getCurrentUser,
} from "../services/authService";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {

  const [user, setUser] = useState(null);

  const [token, setToken] = useState(
    () => sessionStorage.getItem("access_token")
  );

  const [loading, setLoading] = useState(true);


  // Verify existing login session
  useEffect(() => {

    let active = true;

    const verifySession = async () => {

      if (!token) {
        if (active) setLoading(false);
        return;
      }

      try {

        const userData = await getCurrentUser(token);

        if (active) {
          setUser(userData);
        }

      } catch (error) {

        sessionStorage.removeItem("access_token");

        if (active) {
          setToken(null);
          setUser(null);
        }

      } finally {

        if (active) {
          setLoading(false);
        }

      }
    };

    verifySession();

    return () => {
      active = false;
    };

  }, [token]);


  // Login function
  const login = async (credentials) => {

    const response = await loginUser(credentials);

    const accessToken = response.access_token;

    sessionStorage.setItem(
      "access_token",
      accessToken
    );

    setToken(accessToken);

    try {

      const userData = await getCurrentUser(accessToken);

      setUser(userData);

      return userData;

    } catch (error) {

      sessionStorage.removeItem("access_token");
      setToken(null);
      setUser(null);

      throw error;
    }
  };


  // Logout function
  const logout = () => {

    sessionStorage.removeItem("access_token");

    setToken(null);
    setUser(null);

  };


  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        logout,
        isAuthenticated: Boolean(user && token),
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};


// Custom authentication hook
export const useAuth = () => {

  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider"
    );
  }

  return context;
};
