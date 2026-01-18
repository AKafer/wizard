import { useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { loginRequest } from "@/services/auth.service";
import { useNavigate } from "react-router-dom";

export default function LoginPage() {
	const [username, setUsername] = useState("");
	const [password, setPassword] = useState("");
	const [error, setError] = useState(null);
	const [loading, setLoading] = useState(false);

	const { login } = useAuth();
	const navigate = useNavigate();

	const handleSubmit = async (e) => {
		e.preventDefault();
		setLoading(true);
		setError(null);

		try {
			const data = await loginRequest({ username, password });
			login(data.access_token);
			navigate("/admin/certificates");
		} catch (err) {
			setError("Неверный логин или пароль");
			console.error(err);
		} finally {
			setLoading(false);
		}
	};

	return (
		<div style={{ maxWidth: 400, margin: "50px auto" }}>
			<h2>Вход администратора "Сертификаты"</h2>
			<form onSubmit={handleSubmit}>
				<div>
					<label>Пользователь: </label>
					<input
						type="text"
						value={username}
						onChange={(e) => setUsername(e.target.value)}
						required
					/>
				</div>
				<div style={{ marginTop: 10 }}>
					<label>Пароль: </label>
					<input
						type="password"
						value={password}
						onChange={(e) => setPassword(e.target.value)}
						required
					/>
				</div>
				{error && <p style={{ color: "red" }}>{error}</p>}
				<button type="submit" disabled={loading} style={{ marginTop: 15 }}>
					{loading ? "Вход..." : "Войти"}
				</button>
			</form>
		</div>
	);
}
