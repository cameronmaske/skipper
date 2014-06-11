from skipper.groups import Group


class AWSGroup(Group):
    def __init__(self, ec2, *args, **kwargs):
        super(AWSGroup, self).__init__(*args, **kwargs)
        self.ec2 = ec2
