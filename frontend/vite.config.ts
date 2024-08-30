import { fileURLToPath, URL } from "node:url";
import { defineConfig, loadEnv } from "vite";
import solidPlugin from "vite-plugin-solid";

export default ({ mode }: { mode: string }) => {
    // Load environment variables based on the current mode
    const env = loadEnv(mode, process.cwd());

    return defineConfig({
        plugins: [
            // devtools(),
            solidPlugin(),
        ],

        resolve: {
            alias: {
                "@": fileURLToPath(new URL("./src", import.meta.url)),
            },
            conditions: ["development", "browser"],
        },

        server: {
            port: parseInt(env.VITE_PORT as string, 10) || 3000,
        },
    });
};
