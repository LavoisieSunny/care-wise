import api from './client';

export interface AuthUser {
  id: string;
  email: string;
  name: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

export const registerUser = async (
  email: string,
  password: string,
  name: string
): Promise<AuthResponse> => {
  const res = await api.post<AuthResponse>('/auth/register', { email, password, name });
  return res.data;
};

export const loginUser = async (
  email: string,
  password: string
): Promise<AuthResponse> => {
  const res = await api.post<AuthResponse>('/auth/login', { email, password });
  return res.data;
};

export const saveSession = (auth: AuthResponse) => {
  localStorage.setItem('carewise_token', auth.access_token);
  localStorage.setItem('carewise_user', JSON.stringify(auth.user));
};

export const getToken = (): string | null => localStorage.getItem('carewise_token');

export const getStoredUser = (): AuthUser | null => {
  const raw = localStorage.getItem('carewise_user');
  return raw ? JSON.parse(raw) : null;
};

export const logout = () => {
  localStorage.removeItem('carewise_token');
  localStorage.removeItem('carewise_user');
};
