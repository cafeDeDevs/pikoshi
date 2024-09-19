const DB_NAME = "PikoshiGalleryDB";
const STORE_NAME = "Thumbnails";

interface ImageMetadata {
    data: string; // Base64 encoded image data
    type: string; // Metadata field, e.g. "original", "mobile"
    file_name: string; // Name of File
}

const openDB = (): Promise<IDBDatabase> => {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, 1);

        request.onupgradeneeded = event => {
            const db = (event.target as IDBOpenDBRequest).result;
            if (!db.objectStoreNames.contains(STORE_NAME)) {
                db.createObjectStore(STORE_NAME, {
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

export const addThumbnailsToDB = async (images: Array<ImageMetadata>) => {
    const db = await openDB();
    const tx = db.transaction(STORE_NAME, "readwrite");
    const store = tx.objectStore(STORE_NAME);
    for (const image of images) {
        // console.log("image :=>", image);
        const request = store.add(image);
        // store.
        request.onerror = event => {
            console.error(
                `Error adding image ${image.file_name} to IndexeDB!: `,
                event.target,
            );
        };
    }

    tx.onerror = event => {
        console.error("Transaction error while adding images to DB: ", event);
    };
};

export const getThumbnailsFromDB = async (): Promise<Array<ImageMetadata>> => {
    const db = await openDB();
    const tx = db.transaction(STORE_NAME, "readonly");
    const store = tx.objectStore(STORE_NAME);
    return new Promise((resolve, reject) => {
        const request = store.getAll();
        request.onsuccess = () => {
            resolve(request.result);
        };
        request.onerror = event => {
            reject(`Error retrieving images from IndexedDB: ${event.target}`);
        };

        tx.onerror = event => {
            reject(
                `Transaction to get images from IndexedDB failed: ${event.target}`,
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
