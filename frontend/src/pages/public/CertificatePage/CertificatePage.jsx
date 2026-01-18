import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { publicApi } from "@/helpers/PublicApiClient";
import "./certificate.styles.css";
import CertificateCard from "./CertificateCard.jsx";
import telegramIcon from "@/assets/telegram.svg";

// Карточка сертификата


// Страница сертификата
export default function CertificatePage() {
	const { id } = useParams();
	const [certificate, setCertificate] = useState(null);
	const [stage, setStage] = useState("loading"); // loading → shown
	const [offsetY, setOffsetY] = useState(30);   // старт под конвертом +30px

	const BASE_Y = 30;   // старт под конвертом
	const FINAL_Y = 0;   // конечная позиция

	useEffect(() => {
		const fetchCertificate = async () => {
			try {
				const { data } = await publicApi.get(`/certificates/${id}`);
				setCertificate(data);

				// плавный выезд
				setTimeout(() => {
					setOffsetY(FINAL_Y);
					setStage("shown");
				}, 50);
			} catch (e) {
				console.error(e);
			}
		};
		fetchCertificate();
	}, [id]);

	if (!certificate) {
		// пока данных нет — показываем "Подождите"
		return (
			<div className="certificate-page">
				<div className="certificate-wrapper">
					<div className="certificate-scene">
						<img
							src="/images/envelope-back.png"
							alt=""
							className="envelope-back"
						/>
						<div
							className="certificate-card-wrapper"
							style={{
								transform: `translateX(-50%) translateY(${offsetY}px)`,
								transition: "transform 0.6s cubic-bezier(0.22, 1, 0.36, 1)"
							}}
						/>
						<img
							src="/images/envelope-front.png"
							alt=""
							className="envelope-front"
						/>
					</div>
					<div className="certificate-footer">
						<div className="certificate-loading">
							Подождите, загружаем сертификат…
						</div>
					</div>
				</div>
			</div>
		);
	}

	let statusHint = "Статус: ";
	if (certificate.status === "ACTIVE") statusHint = "*Статус: Действует";
	if (certificate.status === "USED") statusHint = "*Статус: Использован";
	if (certificate.status === "EXPIRED") statusHint = "*Статус: Истёк";

	return (
		<div className="certificate-page">
			<div className="certificate-wrapper">
				<div className="certificate-scene">

					<img
						src="/images/envelope-back.png"
						alt=""
						className="envelope-back"
					/>

					<div
						className={`certificate-card-wrapper show`}
						style={{
							transform: `translateX(-50%) translateY(${offsetY}px)`,
							transition: "transform 0.6s cubic-bezier(0.22, 1, 0.36, 1)"
						}}
					>
						<CertificateCard certificate={certificate} />
					</div>

					<img
						src="/images/envelope-front.png"
						alt=""
						className="envelope-front"
					/>
				</div>

				<div className="certificate-footer">
					{stage !== "shown" && (
						<div className="certificate-loading">
							Подождите, загружаем сертификат…
						</div>
					)}

					{stage === "shown" && (
						<div className="certificate-status-hint">
							{statusHint}
						</div>
					)}

					<a
						href="https://antrasha.ru/giftcards"
						target="_blank"
						rel="noopener noreferrer"
						className="certificate-rules-link"
					>
						Правила использования сертификата
					</a>

					{/* Новая строка с Telegram */}
					<a
						href="https://t.me/AntrashaBot"
						target="_blank"
						rel="noopener noreferrer"
						className="certificate-telegram-link"
					>
						<img
							src={telegramIcon}
							alt="Telegram"
							className="telegram-icon"
						/>

					</a>
				</div>


			</div>
		</div>
	);
}
