import { useEffect, useState } from "react";
import { api } from "@/helpers/ApiClient";
import "./ChargeCertificateModal.css";

export default function ChargeCertificateModal({ certificate, onSuccess }) {
	const [step, setStep] = useState("IDLE"); // IDLE | SMS_SENT | SUCCESS

	const [chargeSum, setChargeSum] = useState(certificate.amount);
	const [confirmCode, setConfirmCode] = useState("");

	const [loading, setLoading] = useState(false);
	const [error, setError] = useState(null);

	const [resendTimer, setResendTimer] = useState(0);

	// --- Таймер повторной отправки ---
	useEffect(() => {
		if (resendTimer <= 0) return;

		const id = setInterval(() => {
			setResendTimer((t) => t - 1);
		}, 1000);

		return () => clearInterval(id);
	}, [resendTimer]);

	// --- Отправка SMS ---
	const sendSms = async () => {
		setError(null);

		// Проверка перед отправкой
		if (!chargeSum || chargeSum <= 0) {
			setError("Введите сумму списания от 1 до " + certificate.amount);
			return;
		}

		setLoading(true);

		try {
			await api.post(
				`/certificates/send_confirm_code/${certificate.id}?charge_sum=${chargeSum}`
			);

			setStep("SMS_SENT");
			setResendTimer(60);
		} catch (err) {
			setError(err.response?.data?.detail || "Ошибка отправки SMS");
		} finally {
			setLoading(false);
		}
	};


	// --- Подтверждение списания ---
	const confirmCharge = async () => {
		if (!confirmCode) return;

		setLoading(true);
		setError(null);

		try {
			await api.post(
				`/certificates/charge/${certificate.id}?confirm_code=${confirmCode}`
			);

			setStep("SUCCESS");
		} catch (err) {
			setError(err.response?.data?.detail || "Неверный код подтверждения");
		} finally {
			setLoading(false);
		}
	};

	// --- Валидация суммы ---
	const handleSumChange = (e) => {
		let value = e.target.value;

		// Разрешаем пустое поле
		if (value === "") {
			setChargeSum("");
			return;
		}

		// Только числа
		value = Number(value);
		if (Number.isNaN(value)) return;

		// Ограничиваем сверху
		if (value > certificate.amount) value = certificate.amount;

		setChargeSum(value);
	};



	return (
		<div className="charge-modal">
			{/* --- IDLE / SMS_SENT --- */}
			{step !== "SUCCESS" && (
				<>
					<div className="field">
						<label>Сумма списания</label>
						<input
							type="number"
							value={chargeSum}
							onChange={handleSumChange}
							disabled={step !== "IDLE"}
						/>
						<div className="hint">
							Максимум: {certificate.amount}
						</div>
					</div>

					{step === "IDLE" && (
						<button
							className="primary-btn"
							onClick={sendSms}
							disabled={loading}
						>
							Отправить SMS
						</button>
					)}

					{step === "SMS_SENT" && (
						<>
							<div className="field">
								<label>Код из SMS</label>
								<input
									type="text"
									value={confirmCode}
									onChange={(e) => setConfirmCode(e.target.value)}
									placeholder="Введите код"
								/>
							</div>

							<button
								className="primary-btn"
								onClick={confirmCharge}
								disabled={loading || !confirmCode}
							>
								Подтвердить списание
							</button>

							<button
								className="secondary-btn"
								onClick={sendSms}
								disabled={resendTimer > 0 || loading}
							>
								{resendTimer > 0
									? `Отправить повторно (${resendTimer})`
									: "Отправить повторно"}
							</button>
						</>
					)}
				</>
			)}

			{/* --- SUCCESS (финал) --- */}
			{step === "SUCCESS" && (
				<div className="success-block">
					<div className="success-icon">✅</div>

					<div className="success-text">
						Сертификат успешно списан на сумму <b>{chargeSum}</b>
					</div>

					<div className="success-hint">
						Проведите операцию по кассе.
					</div>

					<button
						className="primary-btn"
						onClick={onSuccess}
					>
						Закрыть
					</button>
				</div>
			)}

			{/* --- ERROR --- */}
			{error && <div className="error-text">{error}</div>}
		</div>
	);
}
