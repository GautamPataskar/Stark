# ML Service
FROM python:3.9-slim as ml-service

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/Stark.ML /app/Stark.ML
COPY models /app/models

CMD ["python", "-m", "Stark.ML.main"]

# API Service
FROM mcr.microsoft.com/dotnet/sdk:6.0 AS build
WORKDIR /src
COPY backend/Stark.API/*.csproj .
RUN dotnet restore
COPY backend/Stark.API .
RUN dotnet publish -c Release -o /app

FROM mcr.microsoft.com/dotnet/aspnet:6.0
WORKDIR /app
COPY --from=build /app .
ENTRYPOINT ["dotnet", "Stark.API.dll"]