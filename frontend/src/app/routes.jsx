import { Navigate } from "react-router-dom";
import AdminLayout from "@/pages/admin/AdminLayout";
import LoginPage from "@/pages/admin/LoginPage";
import DashboardPage from "@/pages/admin/DashboardPage";
import CertificatesPage from "@/pages/admin/CertificatesPage";
import { AdminGuard } from "@/utils/guards";
import CertificatePage from "@/pages/public/CertificatePage/CertificatePage";

export const routes = [
	// Главная редирект на логин
	{ path: "/", element: <Navigate to="/admin/login" replace /> },

	// Публичная страница сертификата — НА ВЕРХНЕМ УРОВНЕ!
	{ path: "/certificates/:id", element: <CertificatePage /> },

	// Логин админки
	{ path: "/admin/login", element: <LoginPage /> },

	// Всё что внутри /admin требует авторизации
	{
		path: "/admin",
		element: <AdminGuard />,  // Guard оборачивает весь /admin
		children: [
			{
				element: <AdminLayout />, // Layout для админки
				children: [
					{ index: true, element: <DashboardPage /> }, // /admin
					{ path: "certificates", element: <CertificatesPage /> }, // /admin/certificates
				],
			},
		],
	},
];
