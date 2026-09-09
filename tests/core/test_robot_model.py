from app.core.models.robot import RobotModel


class TestRobotModel:
    def test_should_clean(self):
        robot = RobotModel.BASIC
        assert robot.should_clean(dirty=True) is True
        assert robot.should_clean(dirty=False) is True  # cleans already-cleaned tiles

        robot = RobotModel.PREMIUM
        assert robot.should_clean(dirty=True) is True
        assert robot.should_clean(dirty=False) is False
