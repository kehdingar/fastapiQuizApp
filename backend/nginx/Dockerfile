# Use an official Nginx runtime as a parent image
FROM nginx:1.21.3-alpine

# Set the working directory to /app
WORKDIR /app

# Copy the Nginx configuration file
COPY nginx.conf /etc/nginx/nginx.conf

# Copy the React build files
COPY build /usr/share/nginx/html

# Expose port 80 for HTTP traffic
EXPOSE 80

# Start Nginx when the container starts
CMD ["nginx", "-g", "daemon off;"]