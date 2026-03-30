
import subprocess


class S3Sync:
    def sync_folder_to_s3(self, folder, aws_bucket_url):
        try:
            command = [
                "aws", "s3", "sync",
                folder,
                aws_bucket_url,
                "--region", "ap-south-1"
            ]

            print("Running command:", " ".join(command))

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )

            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)

        except subprocess.CalledProcessError as e:
            print(" S3 Upload Failed")
            print("Error Output:", e.stderr)
            raise e

    def sync_folder_from_s3(self, folder, aws_bucket_url):
        try:
            command = [
                "aws", "s3", "sync",
                aws_bucket_url,
                folder,
                "--region", "ap-south-1"
            ]

            print("Running command:", " ".join(command))

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )

            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)

        except subprocess.CalledProcessError as e:
            print("S3 Download Failed")
            print("Error Output:", e.stderr)
            raise e
