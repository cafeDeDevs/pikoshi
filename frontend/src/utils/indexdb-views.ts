const DB_NAME = "PikoshiGalleryDB_2";
const STORE_NAME = "Views";

interface ImageMetadata {
    data: string; // Base64 encoded image data
    type: string; // Metadata field, e.g. "original", "mobile"
    file_name: string; // Name of File
}

const openDB = (): Promise<IDBDatabase> => {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, 2);

        request.onupgradeneeded = event => {
            const db = (event.target as IDBOpenDBRequest).result;
            if (!db.objectStoreNames.contains(STORE_NAME)) {
                db.createObjectStore(STORE_NAME, {
                    keyPath: "file_name",
                    autoIncrement: true,
                });
            }
        };

        request.onsuccess = () => {
            resolve(request.result);
        };

        request.onerror = event => {
            reject(`Error opening IndexedDB: ${event.target}`);
        };
    });
};

export const addImageToDB = async (image: ImageMetadata) => {
    const db = await openDB();
    const tx = db.transaction(STORE_NAME, "readwrite");
    const store = tx.objectStore(STORE_NAME);
    const request = store.add(image);
    db.close();
    request.onerror = event => {
        console.error(
            `Error adding image ${image.file_name} to IndexeDB!: `,
            event.target,
        );
    };

    tx.onerror = event => {
        console.error(
            "Transaction error while adding image to DB: ",
            event.target,
        );
    };
};

export const getImageFromDB = async (
    fileName: string,
): Promise<ImageMetadata> => {
    const db = await openDB();
    const tx = db.transaction(STORE_NAME, "readonly");
    const store = tx.objectStore(STORE_NAME);
    return new Promise((resolve, reject) => {
        const request = store.get(fileName);
        db.close();
        request.onsuccess = () => {
            resolve(request.result);
        };
        request.onerror = event => {
            reject(`Error retrieving image from IndexedDB: ${event.target}`);
        };

        tx.onerror = event => {
            reject(
                `Transaction to get image from IndexedDB failed: ${event.target}`,
            );
        };
    });
};

export const clearDB = async () => {
    const db = await openDB();
    const tx = db.transaction(STORE_NAME, "readwrite");
    const store = tx.objectStore(STORE_NAME);
    return new Promise<void>((resolve, reject) => {
        const request = store.clear();
        db.close();

        request.onsuccess = () => {
            resolve();
        };

        request.onerror = event => {
            reject(`Error clearing IndexedDB: ${event.target}`);
        };

        tx.onerror = event => {
            reject(`Transaction to clear IndexedDB failed: ${event.target}`);
        };
    });
};

export const deleteDatabase = async () => {
    const db = await openDB();
    db.close();
    const request = indexedDB.deleteDatabase(DB_NAME);
    return new Promise<void>((resolve, reject) => {
        request.onsuccess = () => {
            console.log(`Database ${DB_NAME} deleted successfully`);
            resolve();
        };

        request.onerror = event => {
            console.error(`Error deleting database ${DB_NAME}:`, event.target);
            reject(event.target);
        };

        request.onblocked = () => {
            console.warn(
                `Delete request for database ${DB_NAME} is blocked. Close all other connections.`,
            );
            reject(new Error("Delete request blocked"));
        };
    });
};
