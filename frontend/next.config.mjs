const isGithubPages = process.env.GITHUB_PAGES === "true";
const repoName = "remote-hiring-radar";

/** @type {import('next').NextConfig} */
const nextConfig = {
  assetPrefix: isGithubPages ? `/${repoName}/` : undefined,
  basePath: isGithubPages ? `/${repoName}` : undefined,
  images: {
    unoptimized: true,
  },
  output: isGithubPages ? "export" : undefined,
  reactStrictMode: true,
};

export default nextConfig;
