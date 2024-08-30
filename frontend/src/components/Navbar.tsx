import { createSignal, Show, type Component } from "solid-js";
import ProfileCard from "./ProfileCard";

import styles from "../css/Navbar.module.css";

const Navbar: Component = () => {
    const [displayProfileCard, setProfileCard] = createSignal<boolean>(false);

    return (
        <div class={styles.NavContainer}>
            <nav class={styles.Navbar}>
                <button
                    class={styles["hamburger-btn"]}
                    onClick={() => {
                        setProfileCard(!displayProfileCard());
                    }}>
                    <svg
                        id='hamburger-icon'
                        xmlns='http://www.w3.org/2000/svg'
                        width='2em'
                        height='2em'
                        viewBox='0 0 48 48'>
                        <g
                            fill='none'
                            stroke='#000'
                            stroke-linecap='round'
                            stroke-linejoin='round'
                            stroke-width='4'>
                            <path d='M7.94971 11.9497H39.9497' />
                            <path d='M7.94971 23.9497H39.9497' />
                            <path d='M7.94971 35.9497H39.9497' />
                        </g>
                    </svg>
                </button>
                <Show when={displayProfileCard()}>
                    <ProfileCard />
                </Show>
            </nav>
        </div>
    );
};

export default Navbar;
