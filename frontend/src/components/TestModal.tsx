import { Show, type Component } from "solid-js";
import { useModalContext } from "../contexts/ModalContext";

import styles from "../css/TestModal.module.css";

// TODO: Move Upload Image Logic Here.
// NOTE: How to tell Gallery to reupload Gallery on image upload??

// TODO: Add image previwer in modal
const TestModal: Component = () => {
    const { isModalOpen, closeModal, handleUploadClick, handleFileChange } =
        useModalContext();

    return (
        <Show when={isModalOpen()}>
            <div class={styles.ModalOverlay}>
                <div class={styles.TestModal}>
                    <h1 class={styles["modal-header"]}>Upload an Image</h1>
                    <input
                        id="file-input"
                        type="file"
                        accept="image/*"
                        style="display: none;"
                        onChange={handleFileChange}
                    />
                    <button onClick={handleUploadClick}>Choose File</button>
                    <button class={styles["close-btn"]} onClick={closeModal}>
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            width="1.03em"
                            height="1.1em"
                            viewBox="0 0 1216 1312">
                            <path
                                fill="currentColor"
                                d="M1202 1066q0 40-28 68l-136 136q-28 28-68 28t-68-28L608 976l-294 294q-28 28-68 28t-68-28L42 1134q-28-28-28-68t28-68l294-294L42 410q-28-28-28-68t28-68l136-136q28-28 68-28t68 28l294 294l294-294q28-28 68-28t68 28l136 136q28 28 28 68t-28 68L880 704l294 294q28 28 28 68"
                            />
                        </svg>
                    </button>
                </div>
            </div>
        </Show>
    );
};

export default TestModal;
