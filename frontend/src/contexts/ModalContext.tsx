import { createSignal, createContext, useContext } from "solid-js";
import type { Accessor, JSX } from "solid-js";

type ModalContextType = {
    isModalOpen: Accessor<boolean>;
    shouldGalleryReload: Accessor<boolean>;
    openModal: () => void;
    closeModal: () => void;
    reloadGallery: () => void;
};

const ModalContext = createContext<ModalContextType>();

export const ModalProvider = (props: {
    children: JSX.Element;
}): JSX.Element => {
    const [isModalOpen, setIsModalOpen] = createSignal(false);
    const [shouldGalleryReload, setShouldGalleryReload] = createSignal(false);

    const openModal = () => setIsModalOpen(true);
    const closeModal = () => setIsModalOpen(false);
    const reloadGallery = () => setShouldGalleryReload(!shouldGalleryReload());

    const value = {
        isModalOpen: isModalOpen,
        shouldGalleryReload: shouldGalleryReload,
        openModal,
        closeModal,
        reloadGallery,
    };

    return (
        <ModalContext.Provider value={value}>
            {props.children}
        </ModalContext.Provider>
    );
};

export const useModalContext = () => {
    const context = useContext(ModalContext);
    if (!context) {
        throw new Error("useModalContext must be used within a ModalProvider");
    }
    return context;
};
