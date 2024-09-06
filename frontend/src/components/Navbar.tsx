import { createSignal, Show, type Component } from "solid-js";
import { useModalContext } from "../contexts/ModalContext";
import ProfileCard from "./ProfileCard";

import styles from "../css/Navbar.module.css";

// TODO: Move SVGs into separate components
const Navbar: Component = () => {
    const [displayProfileCard, setProfileCard] = createSignal<boolean>(false);
    const { openModal } = useModalContext();
    return (
        <>
            <header class={styles.NavContainer}>
                <nav class={styles.Navbar}>
                    <ul class={styles["nav-list"]}>
                        <li class={styles["nav-list-element"]}>
                            <button
                                onClick={openModal}
                                class={styles["upload-btn"]}>
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    width="2em"
                                    height="2em"
                                    viewBox="0 0 24 24">
                                    <path
                                        fill="currentColor"
                                        d="M10 16h4c.55 0 1-.45 1-1v-5h1.59c.89 0 1.34-1.08.71-1.71L12.71 3.7a.996.996 0 0 0-1.41 0L6.71 8.29c-.63.63-.19 1.71.7 1.71H9v5c0 .55.45 1 1 1m-4 2h12c.55 0 1 .45 1 1s-.45 1-1 1H6c-.55 0-1-.45-1-1s.45-1 1-1"></path>
                                </svg>
                            </button>
                        </li>
                        <li>
                            <button
                                class={styles["hamburger-btn"]}
                                onClick={() => {
                                    setProfileCard(!displayProfileCard());
                                }}>
                                <svg
                                    id="hamburger-icon"
                                    xmlns="http://www.w3.org/2000/svg"
                                    width="2em"
                                    height="2em"
                                    viewBox="0 0 48 48">
                                    <g
                                        fill="none"
                                        stroke="#000"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                        stroke-width="4">
                                        <path d="M7.94971 11.9497H39.9497" />
                                        <path d="M7.94971 23.9497H39.9497" />
                                        <path d="M7.94971 35.9497H39.9497" />
                                    </g>
                                </svg>
                            </button>
                        </li>
                    </ul>
                    <Show when={displayProfileCard()}>
                        <ProfileCard />
                    </Show>
                </nav>
            </header>
        </>
    );
};

export default Navbar;
