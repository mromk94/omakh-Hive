# syntax=docker/dockerfile:1

# Install dependencies
FROM node:20-bullseye AS deps
WORKDIR /app
RUN apt-get update && apt-get install -y \
  python3 make g++ pkg-config libusb-1.0-0-dev \
  && rm -rf /var/lib/apt/lists/*
COPY package.json package-lock.json* ./
RUN npm ci --legacy-peer-deps

# Build the Next.js app
FROM node:20-bullseye AS builder
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Production image
FROM node:20-bullseye-slim AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user (Debian)
RUN groupadd -g 1001 nodejs \
  && useradd -m -u 1001 -g nodejs -s /usr/sbin/nologin nextjs

# Copy necessary files
COPY --from=builder /app/.next ./.next
COPY --from=deps /app/node_modules ./node_modules
COPY package.json ./

# Expose and run
ENV PORT=8080
EXPOSE 8080
USER nextjs
CMD ["npm", "run", "start", "--", "-p", "8080"]
