import { Outlet, Link } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { useState } from "react";
import { CertificateFormModal } from "@/components/CertificateFormModal/CertificateFormModal";

export default function AdminLayout() {
	const { logout } = useAuth();
	const [isModalOpen, setModalOpen] = useState(false);
	const [refreshKey, setRefreshKey] = useState(0); // для обновления таблицы после создания

	return (
		<div>
			<header style={{ padding: 10, background: "#eee", display: "flex", alignItems: "center" }}>
				<div style={{ flexGrow: 1 }}>
					<Link to="/admin" style={{ marginRight: 10 }}>Дашборд</Link>
					<Link to="/admin/certificates" style={{ marginRight: 10 }}>Сертификаты</Link>
				</div>
				<div style={{ flexGrow: 1 }}>
					<button onClick={() => setModalOpen(true)}>Создать сертификат</button>
				</div>

				<button onClick={logout}>Выход</button>
			</header>

			<main>
				<Outlet key={refreshKey} />
			</main>

			<CertificateFormModal
				isOpen={isModalOpen}
				onClose={() => setModalOpen(false)}
				onCreated={() => setRefreshKey((k) => k + 1)}
			/>
		</div>
	);
}
