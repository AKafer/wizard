import axios from "axios";

const raw = (import.meta.env.VITE_API_URL || "").trim();
const apiBase =
  raw && raw !== "undefined" && raw !== "null" ? raw : "/api/v1";

export const publicApi = axios.create({
	baseURL: apiBase,
});
