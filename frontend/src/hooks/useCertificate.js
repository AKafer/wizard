import { useEffect, useState } from "react";
import { getCertificateById } from "@/services/certificates.service";

export const useCertificate = (id) => {
	const [certificate, setCertificate] = useState(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState(null);

	useEffect(() => {
		if (!id) return;

		setLoading(true);

		getCertificateById(id)
			.then(setCertificate)
			.catch(setError)
			.finally(() => setLoading(false));
	}, [id]);

	return { certificate, loading, error };
};
