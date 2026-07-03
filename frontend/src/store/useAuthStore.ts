import { create } from "zustand";

import { clearAuthSession, getStoredAuthSession, saveAuthSession } from "../services/api";
import type { AuthResponse, User } from "../types/api";

interface AuthState {
  token?: string;
  user?: User;
  setSession: (session: AuthResponse) => void;
  logout: () => void;
}

const storedSession = getStoredAuthSession();

export const useAuthStore = create<AuthState>((set) => ({
  token: storedSession?.token,
  user: storedSession?.user,
  setSession: (session) => {
    saveAuthSession({ token: session.access_token, user: session.user });
    set({ token: session.access_token, user: session.user });
  },
  logout: () => {
    clearAuthSession();
    set({ token: undefined, user: undefined });
  },
}));
