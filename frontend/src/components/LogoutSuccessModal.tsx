import { Show, type Component } from "solid-js";
import { useModalContext } from "../contexts/ModalContext";

import styles from "../css/LogoutSuccessModal.module.css";

// TODO: Add image previwer in modal
// TODO: compartmentalize out all SVG images
// TODO: Add input fields so that User can title, describe, etc. their image uploads
// i.e. provide meta data for accessibility and file references (make some fields required).
const LogoutSuccessModal: Component = () => {
    const { isLogoutModalOpen } = useModalContext();

    return (
        <Show when={isLogoutModalOpen()}>
            <div class={styles.ModalOverlay}>
                <div class={styles.LogoutSuccessModal}>
                    <h1 class={styles["modal-header"]}>
                        You Have
                        <br />
                        Logged Out Successfully!
                    </h1>
                    <p>Redirecting you...</p>
                </div>
            </div>
        </Show>
    );
};

export default LogoutSuccessModal;
