import { createContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
	const navigate = useNavigate();
	const [token, setToken] = useState(
		localStorage.getItem("jwt_token") || null
	);

	const login = (newToken) => {
		localStorage.setItem("jwt_token", newToken);
		setToken(newToken);
	};

	const logout = () => {
		localStorage.removeItem("jwt_token");
		setToken(null);
	};

	useEffect(() => {
		const handleUnauthorized = () => {
			logout();
			navigate("/admin/login", { replace: true });
		};

		window.addEventListener("unauthorized", handleUnauthorized);

		return () => {
			window.removeEventListener("unauthorized", handleUnauthorized);
		};
	}, [navigate]);

	return (
		<AuthContext.Provider value={{ token, login, logout }}>
			{children}
		</AuthContext.Provider>
	);
};
