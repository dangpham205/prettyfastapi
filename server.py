import uvicorn
from applications import PrettyFastAPI

def main():
    application = PrettyFastAPI()
    uvicorn.run(
        app=application,
        port=3000,
        log_level="info",
        use_colors=True,
    )

if __name__ == "__main__":
    main()
