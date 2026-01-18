import styles from "./Modal.module.css";

export const Modal = ({
						  isOpen,
						  title,
						  onClose,
						  children,
						  width = 450,
						  closeOnOverlayClick = true,
					  }) => {
	if (!isOpen) return null;

	const handleOverlayClick = (e) => {
		if (!closeOnOverlayClick) return;
		if (e.target === e.currentTarget) {
			onClose?.();
		}
	};

	return (
		<div className={styles.overlay} onClick={handleOverlayClick}>
			<div className={styles.modal} style={{ width }} onClick={(e) => e.stopPropagation()}>
				{/* 🔹 крестик первым */}
				<button
					className={styles.closeBtn}
					onClick={onClose}
					aria-label="Закрыть"
				>
					×
				</button>

				{/* Заголовок */}
				{title && <h2 className={styles.modalTitle}>{title}</h2>}

				{children}
			</div>

		</div>
	);
};
