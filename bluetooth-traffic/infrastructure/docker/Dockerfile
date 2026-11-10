FROM eclipse-temurin:21-jre-noble
RUN useradd --system --uid 10001 app
USER 10001
COPY target/app.jar /app/app.jar
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
