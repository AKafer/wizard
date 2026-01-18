import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";

export const AdminGuard = () => {
	const { token } = useAuth();

	// если нет токена → редирект на страницу логина
	if (!token) return <Navigate to="/admin/login" replace />;

	// если токен есть → рендерим вложенные страницы
	return <Outlet />;
};
