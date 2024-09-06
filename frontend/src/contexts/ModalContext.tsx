import {
    createSignal,
    createContext,
    useContext,
    type JSX,
    type Accessor,
} from "solid-js";

type ModalContextType = {
    isModalOpen: Accessor<boolean>;
    openModal: () => void;
    closeModal: () => void;
    handleUploadClick: () => void;
    handleFileChange: (e: Event) => void;
};

const ModalContext = createContext<ModalContextType>();

export const ModalProvider = (props: {
    children: JSX.Element;
}): JSX.Element => {
    const [isModalOpen, setIsModalOpen] = createSignal(false);
    const [files, setFiles] = createSignal<File[]>([]);

    const openModal = () => setIsModalOpen(true);
    const closeModal = () => setIsModalOpen(false);

    const handleUploadClick = () => {
        const input = document.getElementById("file-input") as HTMLInputElement;
        if (input) input.click();
    };

    const handleFileChange = (e: Event) => {
        const target = e.target as HTMLInputElement;
        if (target.files) {
            setFiles([...files(), target.files[0]]);
        }
    };

    const value = {
        isModalOpen,
        openModal,
        closeModal,
        handleUploadClick,
        handleFileChange,
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
