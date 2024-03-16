resource "aws_instance" "messageservice" {
  ami           = data.aws_ami.al2023.id
  instance_type = "t3.micro"
  user_data     = file("userdata.sh")
  tags          = {
    Name    = "MessageService"
    Service = "MessageService"
  }
}
