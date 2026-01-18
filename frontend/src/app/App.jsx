import { useRoutes } from "react-router-dom";
import { routes } from "./routes"; // твой routes.jsx

export default function App() {
	const element = useRoutes(routes);
	return element;
}
