export default function CertificateCard({ certificate }) {
	const {
		amount,
		phone,
		code,
		status,
		indefinite,
		created_at,
		period,
	} = certificate;

	const statusIcon = status === "ACTIVE" ? "" : "❌";

	const getValidUntil = () => {
		if (indefinite) return "бессрочно";

		if (!created_at || !period) return "бессрочно";

		const createdDate = new Date(created_at);
		const validUntil = new Date(createdDate);
		validUntil.setDate(validUntil.getDate() + period);

		return validUntil.toLocaleDateString("ru-RU", {
			day: "numeric",
			month: "long",
			year: "numeric",
		});
	};

	return (
		<div className="certificate-card">
			<h2>Сертификат {code}</h2>

			<p style={{ fontSize: "16px", margin: "8px 0" }}>
				На сумму <strong>{amount}</strong> ₽
			</p>

			<p>Владелец: {phone}</p>

			<p>
				Действителен до: {getValidUntil()}
			</p>

			<div className="certificate-status-icon">{statusIcon}</div>
		</div>
	);
}
