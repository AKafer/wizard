import { api } from "@/helpers/ApiClient";

export const loginRequest = async ({ username, password }) => {
	const params = new URLSearchParams();
	params.append("grant_type", "password");
	params.append("username", username);
	params.append("password", password);
	params.append("scope", "");
	params.append("client_id", null);
	params.append("client_secret", null);

	const { data } = await api.post("auth/jwt/login", params, {
		headers: {
			"Content-Type": "application/x-www-form-urlencoded",
			"Accept": "application/json",
		},
	});

	return data;
};
