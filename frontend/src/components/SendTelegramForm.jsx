import { useState } from "react";
import styles from "./SendTelegramForm.module.css";
import {api} from "@/helpers/ApiClient.js";


export const SendTelegramForm = ({ certificate, onClose }) => {
	const [telegramId, setTelegramId] = useState("");
	const [loading, setLoading] = useState(false);

	const send = async () => {
	  if (!telegramId) return alert("Введите Telegram ID");

	  setLoading(true);
	  try {
		const payload = {
		  chat_id: Number(telegramId),
		  image_url: "https://storage.yandexcloud.net/files-for-sites/sert2.png",
		};

		const res = await api.post(`/certificates/send_telegram_msg/${certificate.id}`, payload);

		alert("Отправлено в Telegram");
		onClose();
	  } catch (err) {
		console.error(err);

		// axios-style:
		const detail =
		  err?.response?.data?.detail ||
		  err?.response?.data?.message ||
		  err?.message ||
		  "Ошибка отправки";

		alert("Ошибка отправки: " + detail);
	  } finally {
		setLoading(false);
	  }
	};


	return (
		<div className={styles.form}>
			<p>
				Сертификат: <b>{certificate.code}</b>
			</p>

			<input
				placeholder="Telegram ID"
				value={telegramId}
				onChange={(e) => setTelegramId(e.target.value)}
			/>

			<div className={styles.actions}>
				<button onClick={onClose}>Отмена</button>
				<button onClick={send} disabled={loading}>
					{loading ? "Отправка..." : "Отправить"}
				</button>
			</div>
		</div>
	);
};
