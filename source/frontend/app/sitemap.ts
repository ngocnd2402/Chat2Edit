import { MetadataRoute } from "next";

const routes = [
    "/",
    "/features",
    "/about",
    "/contact",
]

export default function sitemap(): MetadataRoute.Sitemap {
    return routes.map((route) => ({ url: route }));
}