# Hackathon AWS usage rules

Read from the organizer's 10 October 2026 email, “AWS setup & usage rules for your team — neatHack”. [Open the email](https://mail.google.com/mail/u/?authuser=sandeshdawkhar13%40gmail.com#all/1a123ff19ef3e3f6).

- Use only us-east-1 and the existing Hackathon_VPC; do not create a VPC.
- Permitted services: EC2, Lambda, IAM roles and load balancers.
- One EC2 instance per supplied IAM user. Terminate an existing instance before creating a replacement.
- Permitted instance families/sizes: t2, t3 and t3a, nano through large.
- Each EBS volume must be at most 50 GB.
- The team shares a USD25 allowance; no additional credits, accounts or payment cards.
- Stop resources when finished. The access page is not a spending meter. Keep CLI credentials private.

Bakaya uses one dedicated t3.small with standard CPU credits, IMDSv2 and a 16 GB gp3 volume. Other users' instances are untouched. No extra load balancer or NAT gateway was created.

The email does not establish KMS permission. The encrypted launch omitted KmsKeyId and still failed with Client.InvalidKMSKey.InvalidState. After the provider suggested default EBS, the owner explicitly approved an unencrypted synthetic-data demo on 11 October. Real financial documents remain excluded from that deployment. This exception does not establish production storage readiness.

AWS costs are separate from the model provider's USD15/key/30-day allowance and Crustdata's 500-credit limit. Instance, disk, public IPv4 and traffic charges consume the shared AWS budget; stop the demo after the event and check remaining resources.
