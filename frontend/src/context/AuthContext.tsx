import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type PropsWithChildren,
} from "react";

import { authApi } from "../api/auth";
import { ApiError } from "../api/client";
import { clearAuthToken, getAuthToken, setAuthToken } from "../utils/authToken";
import type { UserLogin, UserResponse } from "../types/auth";

type AuthContextValue = {
  user: UserResponse | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (payload: UserLogin) => Promise<void>;
  register: (email: string, password: string, displayName?: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadUser = useCallback(async () => {
    const token = getAuthToken();
    if (!token) {
      setUser(null);
      setIsLoading(false);
      return;
    }

    try {
      const profile = await authApi.me();
      setUser(profile);
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        clearAuthToken();
      }
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadUser();
  }, [loadUser]);

  const login = useCallback(async (payload: UserLogin) => {
    const response = await authApi.login(payload);
    setAuthToken(response.access_token);
    const profile = await authApi.me();
    setUser(profile);
  }, []);

  const register = useCallback(async (email: string, password: string, displayName?: string) => {
    await authApi.register({ email, password, display_name: displayName });
    await login({ email, password });
  }, [login]);

  const logout = useCallback(() => {
    clearAuthToken();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({
      user,
      isLoading,
      isAuthenticated: user !== null,
      login,
      register,
      logout,
    }),
    [user, isLoading, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
