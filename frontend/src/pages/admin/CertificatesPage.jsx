import { useEffect, useState, useMemo } from "react";
import { Link } from "react-router-dom";
import {
	useTable,
	useSortBy,
	useGlobalFilter,
} from "react-table";
import "./CertificatesTable.css";
import { Modal } from "@/components/ui/Modal";
import { SendTelegramForm } from "@/components/SendTelegramForm";
import ChargeCertificateModal from "@/components/ChargeCertificateModal.jsx";
import {api} from "@/helpers/ApiClient.js";
import telegramIcon from "@/assets/telegram.svg";

// Форматирование даты по-русски
const formatDateRu = (date) => {
	if (!date) return "—";
	return new Date(date).toLocaleDateString("ru-RU", {
		day: "numeric",
		month: "long",
		year: "numeric",
	});
};

// Срок действия сертификата
const getExpirationText = (c) => {
	if (c.indefinite) return "бессрочно";
	if (!c.created_at || !c.period) return "—";
	const d = new Date(c.created_at);
	d.setDate(d.getDate() + c.period);
	return `до ${formatDateRu(d)}`;
};

// Стили статусов
const statusStyles = {
	ACTIVE: "status-active",
	USED: "status-used",
	EXPIRED: "status-expired",
};

export default function CertificatesPage() {
	const [certificates, setCertificates] = useState([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState(null);

	const [globalFilter, setGlobalFilter] = useState("");
	const [onlyActive, setOnlyActive] = useState(true);

	const [tgCert, setTgCert] = useState(null);
	const [chargeCert, setChargeCert] = useState(null);

	// --- Telegram modal ---
	const openTelegramModal = (certificate) => {
		setTgCert(certificate);
	};

	const closeTelegramModal = () => {
		setTgCert(null);
	};

	// --- Загрузка сертификатов ---
	const fetchCertificates = async () => {
		setLoading(true);
		try {
			const res = await api.get("/certificates/");
			setCertificates(res.data);
		} catch (err) {
			console.error(err);
			setError("Ошибка при загрузке сертификатов");
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		fetchCertificates();
	}, []);

	// --- Фильтрация ---
	const filteredData = useMemo(() => {
		if (!onlyActive) return certificates;
		return certificates.filter((c) => c.status === "ACTIVE");
	}, [certificates, onlyActive]);

	// --- Колонки таблицы ---
	const columns = useMemo(
		() => [
			{
				Header: "Код",
				accessor: "code",
				Cell: ({ row }) => (
					<Link
						to={`/certificates/${row.original.id}`}
						className="code-link"
					>
						{row.original.code}
					</Link>
				),
			},
			{ Header: "Номинал", accessor: "nominal" },
			{ Header: "Остаток", accessor: "amount" },
			{
				Header: "Описание",
				accessor: "description",
				Cell: ({ value }) => value || "—",
			},
			{
				Header: "Телефон",
				accessor: "phone",
				Cell: ({ value }) => value || "—",
			},
			{
				Header: "Сотрудник",
				accessor: "employee",
				Cell: ({ value }) => value || "—",
			},
			{
				Header: "Дата выдачи",
				accessor: "created_at",
				Cell: ({ value }) => formatDateRu(value),
			},
			{
				Header: "Срок действия",
				accessor: (row) => getExpirationText(row),
			},
			{
				Header: "Статус",
				accessor: "status",
				Cell: ({ value }) => (
					<span className={`status-badge ${statusStyles[value] || ""}`}>
						{value}
					</span>
				),
			},
			{
				Header: "",
				id: "telegram",
				Cell: ({ row }) => (
					<button
						className="tg-btn"
						title="Отправить в Telegram"
						onClick={() => openTelegramModal(row.original)}
					>
						<img src={telegramIcon} alt="Telegram" />
					</button>
				),
			},
			{
				Header: "Списать",
				id: "charge",
				Cell: ({ row }) => {
					const cert = row.original;
					return (
						<button
							className="charge-btn"
							title="Списать сертификат"
							disabled={cert.status !== "ACTIVE"}
							onClick={() => setChargeCert(cert)}
						>
							💳
						</button>
					);
				},
			},
		],
		[]
	);

	const tableInstance = useTable(
		{
			columns,
			data: filteredData,
			globalFilter,
		},
		useGlobalFilter,
		useSortBy
	);

	const {
		getTableProps,
		getTableBodyProps,
		headerGroups,
		rows,
		prepareRow,
		setGlobalFilter: setTableFilter,
	} = tableInstance;

	useEffect(() => {
		setTableFilter(globalFilter);
	}, [globalFilter, setTableFilter]);

	if (loading) return <p className="p-6">Загрузка сертификатов…</p>;
	if (error) return <p className="p-6 text-red-600">{error}</p>;

	return (
		<div className="cert-container">
			<h2>Список сертификатов</h2>

			<div className="filters-row">
				<input
					type="text"
					placeholder="Поиск..."
					value={globalFilter}
					onChange={(e) => setGlobalFilter(e.target.value)}
					className="global-search"
				/>

				<label className="active-filter">
					<input
						type="checkbox"
						checked={onlyActive}
						onChange={(e) => setOnlyActive(e.target.checked)}
					/>
					<span>Показать только действующие</span>
				</label>
			</div>

			<div className="table-wrapper">
				<table {...getTableProps()}>
					<thead>
					{headerGroups.map((headerGroup) => {
						const { key, ...props } =
							headerGroup.getHeaderGroupProps();
						return (
							<tr key={key} {...props}>
								{headerGroup.headers.map((column) => {
									const { key, ...props } =
										column.getHeaderProps(
											column.getSortByToggleProps()
										);
									return (
										<th key={key} {...props}>
											{column.render("Header")}
											{column.isSorted &&
												(column.isSortedDesc
													? " 🔽"
													: " 🔼")}
										</th>
									);
								})}
							</tr>
						);
					})}
					</thead>

					<tbody {...getTableBodyProps()}>
					{rows.map((row) => {
						prepareRow(row);
						const { key, ...props } = row.getRowProps();
						return (
							<tr key={key} {...props}>
								{row.cells.map((cell) => {
									const { key, ...props } =
										cell.getCellProps();
									return (
										<td key={key} {...props}>
											{cell.render("Cell")}
										</td>
									);
								})}
							</tr>
						);
					})}
					</tbody>
				</table>
			</div>

			{/* --- Telegram --- */}
			<Modal
				isOpen={!!tgCert}
				title="Отправить в Telegram"
				onClose={closeTelegramModal}
				width={500}
			>
				{tgCert && (
					<SendTelegramForm
						certificate={tgCert}
						onClose={closeTelegramModal}
					/>
				)}
			</Modal>

			{/* --- Списание сертификата --- */}
			<Modal
				isOpen={!!chargeCert}
				title="Списание сертификата"
				onClose={() => setChargeCert(null)}
				width={400}
				closeOnOverlayClick={false} // 🔹 теперь реально блокирует закрытие
			>
				{chargeCert && (
					<ChargeCertificateModal
						certificate={chargeCert}
						onSuccess={() => {
							fetchCertificates();
							setChargeCert(null);
						}}
					/>
				)}
			</Modal>


		</div>
	);
}
