a = read.table("Documents/CS6200/Homework5/152101")
b = read.table("Documents/CS6200/Homework5/152102")
c = read.table("Documents/CS6200/Homework5/152103")

pdf("Documents/CS6200/Homework5/precision-recall_curves.pdf")
plot(a$V1, a$V2, type = 'l', xlab="recall", ylab="precision", main="152101", col="red")
plot(b$V1, b$V2, type = 'l', xlab="recall", ylab="precision", main="152102", col="red")
plot(c$V1, c$V2, type = 'l', xlab="recall", ylab="precision", main="152103", col="red")
dev.off()
