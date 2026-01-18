import axios from "axios";
import {
	getToken,
	setToken,
	getRefreshToken,
	clearToken,
} from "./tokenStorage";

const raw = (import.meta.env.VITE_API_URL || "").trim();
const apiBase =
  raw && raw !== "undefined" && raw !== "null" ? raw : "/api/v1";

export const api = axios.create({
	baseURL: apiBase,
	withCredentials: true,
});

// ===== REQUEST =====
api.interceptors.request.use((config) => {
	const token = getToken();
	if (token) {
		config.headers.Authorization = `Bearer ${token}`;
	}
	return config;
});

// ===== RESPONSE =====
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
	failedQueue.forEach((prom) => {
		if (error) prom.reject(error);
		else prom.resolve(token);
	});
	failedQueue = [];
};

api.interceptors.response.use(
	(response) => response,
	async (error) => {
		const originalRequest = error.config;

		// если это не 401 — просто ошибка
		if (error.response?.status !== 401) {
			return Promise.reject(error);
		}

		// защита от бесконечного цикла
		if (originalRequest._retry) {
			clearToken();
			window.dispatchEvent(new Event("unauthorized"));
			return Promise.reject(error);
		}

		const refreshToken = getRefreshToken();
		if (!refreshToken) {
			clearToken();
			window.dispatchEvent(new Event("unauthorized"));
			return Promise.reject(error);
		}

		// если refresh уже идёт — ставим запрос в очередь
		if (isRefreshing) {
			return new Promise((resolve, reject) => {
				failedQueue.push({
					resolve: (token) => {
						originalRequest.headers.Authorization = `Bearer ${token}`;
						resolve(api(originalRequest));
					},
					reject,
				});
			});
		}

		originalRequest._retry = true;
		isRefreshing = true;

		try {
			const res = await api.post("auth/jwt/refresh", null, {
			  params: { refresh_token: refreshToken },
			});

			const newToken = res.data.jwt_token;
			setToken(newToken);

			api.defaults.headers.Authorization = `Bearer ${newToken}`;
			processQueue(null, newToken);

			return api(originalRequest);
		} catch (refreshError) {
			processQueue(refreshError, null);
			clearToken();
			window.dispatchEvent(new Event("unauthorized"));
			return Promise.reject(refreshError);
		} finally {
			isRefreshing = false;
		}
	}
);
