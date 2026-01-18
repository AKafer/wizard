import { useState } from "react";
import { api } from "@/helpers/ApiClient";
import styles from "./CertificateFormModal.module.css";

export const CertificateFormModal = ({ isOpen, onClose, onCreated }) => {
	const [form, setForm] = useState({
		nominal: 0,
		check_amount: 0,
		description: "",
		employee: "Олеся",
		created_at: new Date().toISOString().split("T")[0],
		indefinite: true,
		period: 0,
		name: "",
		last_name: "",
		phone: "",
	});

	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");

	// Для телефона и суммы
	const handleChange = (e) => {
		const { name, value, type, checked } = e.target;
		let val;

		if (name === "phone") {
			// оставляем только цифры после 7
			val = value.replace(/\D/g, ""); // все нецифры убираем
			if (!val.startsWith("7")) val = "7" + val.slice(0, 10); // фиксируем 7
			val = val.slice(0, 11); // максимум 11 символов
		} else if (type === "checkbox") {
			val = checked;
		} else if (type === "number") {
			val = value === "" ? "" : Math.floor(Number(value)); // целые числа
		} else {
			val = value;
		}

		setForm((prev) => ({
			...prev,
			[name]: val,
		}));
	};


	const handleSubmit = async (e) => {
		e.preventDefault();
		setLoading(true);
		setError("");

		try {
			await api.post("/certificates/", { ...form, status: "ACTIVE", check_amount: 0 });
			onCreated?.();
			onClose();
		} catch (err) {
			console.error(err);
			setError("Ошибка при создании сертификата");
		} finally {
			setLoading(false);
		}
	};

	if (!isOpen) return null;

	return (
		<div className={styles.overlay}>
			<div className={styles.modal}>
				<h2>Создать сертификат</h2>
				<form onSubmit={handleSubmit} className={styles.form}>
					<div className={styles.row}>
						<label>Имя</label>
						<input
							name="name"
							value={form.name}
							onChange={handleChange}
							placeholder="Имя"
						/>
					</div>

					<div className={styles.row}>
						<label>Фамилия</label>
						<input
							name="last_name"
							value={form.last_name}
							onChange={handleChange}
							placeholder="Фамилия"
						/>
					</div>

					<div className={styles.row}>
						<label>Телефон *</label>
						<input
							name="phone"
							value={form.phone}
							onChange={handleChange}
							placeholder="7**********"
							required
							maxLength={11}
							onFocus={(e) => {
								if (!e.target.value.startsWith("7")) {
									e.target.value = "7";
								}
								e.target.setSelectionRange(1, 1); // курсор после 7
							}}
						/>
					</div>

					<div className={styles.row}>
						<label>Сумма</label>
						<input
							name="nominal"
							type="number"
							value={form.nominal === 0 ? "" : form.nominal}
							onChange={handleChange}
							min={0}
							placeholder="Сумма"
							style={{ MozAppearance: "textfield" }}
						/>
					</div>

					<div className={styles.row}>
						<label>Описание</label>
						<input
							name="description"
							value={form.description}
							onChange={handleChange}
							placeholder="Описание"
						/>
					</div>

					<div className={styles.row}>
						<label>Сотрудник</label>
						<select name="employee" value={form.employee} onChange={handleChange}>
							<option>Олеся</option>
							<option>Руслан</option>
							<option>Кристина</option>
							<option>Екатерина</option>
						</select>
					</div>

					<div className={styles.row}>
						<label>Бессрочный</label>
						<input
							name="indefinite"
							type="checkbox"
							checked={form.indefinite}
							onChange={handleChange}
						/>
					</div>

					<div className={styles.row}>
						<label>Период (дней)</label>
						<input
							name="period"
							type="number"
							value={form.period === 0 ? "" : form.period}
							onChange={handleChange}
							disabled={form.indefinite}
						/>
					</div>

					{error && <p className={styles.error}>{error}</p>}

					<div className={styles.actions}>
						<button type="submit" disabled={loading}>
							{loading ? "Создание..." : "Создать"}
						</button>
						<button type="button" onClick={onClose} className={styles.cancel}>
							Отмена
						</button>
					</div>
				</form>
			</div>
		</div>
	);
};
