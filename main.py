import os, sys
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from flask import Flask,jsonify

app = Flask(__name__)
Base = declarative_base()
 
@app.route("/leaderboard/<level>")
def FlaskScores(level):
    return jsonify(highscores=[i.serialize for i in GetLeaderboard(level)])
    
@app.route("/insert/<string:level>/<string:player>/<int:points>")
def FlaskInsert(level,player,points):
    exit = InsertHighscore(level,player,int(points))
    return jsonify(result = exit)
    
class Score(Base):
    __tablename__ = 'scores'
    uniqueId = Column(Integer, primary_key=True)
    level = Column(String(255), nullable=False)
    name = Column(String(18), nullable=False)
    score = Column(Integer, nullable=False)
    
    @property
    def serialize(self):
       return {
           'name': self.name,
           'score': self.score,
       }

def CreateDatabase():
    engine = create_engine('sqlite:///scores.db')
    Base.metadata.create_all(engine)

def Insert(level,player,points):
    engine = create_engine('sqlite:///scores.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    score = Score(level = level, name = player, score=points)
    session.add(score)
    session.commit()

# Insert the highscore in the database if necessary.
# Return 0 if the score replaces an older highscore, 1 if there were less than 10 highscores, and -1 if it wasn't added
def InsertHighscore(level,player,points):    
    engine = create_engine('sqlite:///scores.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker()
    DBSession.bind = engine
    session = DBSession()
    scores = session.query(Score).filter(and_(Score.level == level)).all()
    if len(scores) < 10:
        Insert(level,player,points)
        return 1
    else:
        minScore = scores[0].score
        minId = scores[0].uniqueId
        for item in scores:
            if item.score < minScore:
                minScore = item.score
                minId = item.uniqueId
        if points > minScore:
            session.delete(session.query(Score).get(minId))
            session.commit()
            Insert(level,player,points)
            return 0
        return -1
        
def GetLeaderboard(level):
    engine = create_engine('sqlite:///scores.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker()
    DBSession.bind = engine
    session = DBSession()
    return session.query(Score).filter(and_(Score.level == level)).all()

if __name__ == "__main__":
    CreateDatabase()
    app.run()