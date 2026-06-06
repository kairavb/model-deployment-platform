import { apiRequest } from "./client";
import type { TokenResponse, UserCreate, UserLogin, UserResponse } from "../types/auth";

export const authApi = {
  register(payload: UserCreate) {
    return apiRequest<UserResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  login(payload: UserLogin) {
    return apiRequest<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  me() {
    return apiRequest<UserResponse>("/auth/me");
  },
};
