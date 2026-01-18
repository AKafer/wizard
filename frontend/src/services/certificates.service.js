import { api } from "@/helpers/ApiClient";

export const getCertificateById = async (id) => {
	const response = await api.get(`/certificates/${id}`);
	return response.data;
};
