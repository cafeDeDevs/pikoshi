import { createSignal, createContext, useContext } from "solid-js";
import type { Accessor, JSX } from "solid-js";

interface ImageMetadata {
    data: string; // Base64 encoded image data
    type: string; // Metadata field, e.g. "original", "mobile"
    file_name: string; // Name of File
}

type ModalContextType = {
    isModalOpen: Accessor<boolean>;
    isImageModalOpen: Accessor<boolean>;
    shouldGalleryReload: Accessor<boolean>;
    selectedImage: Accessor<ImageMetadata | null>;
    openModal: () => void;
    openImageModal: (image: ImageMetadata | null) => void;
    closeModal: () => void;
    closeImageModal: () => void;
    reloadGallery: () => void;
};

const ModalContext = createContext<ModalContextType>();

export const ModalProvider = (props: {
    children: JSX.Element;
}): JSX.Element => {
    const [isModalOpen, setIsModalOpen] = createSignal(false);
    const [isImageModalOpen, setIsImageModalOpen] = createSignal(false);
    const [shouldGalleryReload, setShouldGalleryReload] = createSignal(false);
    const [selectedImage, setSelectedImage] =
        createSignal<ImageMetadata | null>(null);

    const openModal = () => setIsModalOpen(true);
    const closeModal = () => setIsModalOpen(false);
    const reloadGallery = () => setShouldGalleryReload(!shouldGalleryReload());

    const openImageModal = (image: ImageMetadata | null) => {
        setSelectedImage(image);
        setIsImageModalOpen(true);
    };

    const closeImageModal = () => {
        setSelectedImage(null);
        setIsImageModalOpen(false);
    };

    const value = {
        isModalOpen: isModalOpen,
        isImageModalOpen: isImageModalOpen,
        shouldGalleryReload: shouldGalleryReload,
        selectedImage: selectedImage,
        openModal,
        openImageModal,
        closeModal,
        closeImageModal,
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
