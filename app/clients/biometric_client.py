import httpx
from uuid import UUID

class BiometricClient:
    def __init__(self):
        self.base_url = "http://localhost:5004/api/biometrics"

    async def enroll(self, user_id: UUID, samples: list[str]):
        async with httpx.AsyncClient(verify=False, timeout=60) as client:
            response = await client.post(f"{self.base_url}/enroll", json={ "userId": str(user_id), "samples": samples })

            response.raise_for_status()

            return response.json()

    async def verify(self, user_id: UUID, sample: str):
        async with httpx.AsyncClient(verify=False, timeout=60) as client:
            response = await client.post(f"{self.base_url}/verify", json={ "userId": str(user_id), "sample": sample })

            response.raise_for_status()

            return response.json()

    async def identify(self, sample: str):
        async with httpx.AsyncClient(verify=False, timeout=60) as client:
            response = await client.post(f"{self.base_url}/identify", json={ "sample": sample })

            response.raise_for_status()

            return response.json()